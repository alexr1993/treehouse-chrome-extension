package com.alexremedios.subredditfinderservice;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.JavaType;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategy;
import com.google.common.collect.ImmutableMap;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

import javax.servlet.http.HttpServletRequest;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@Slf4j
public class SubmissionController {
    private final static String QUEUE_NAME = "request queue";
    private final Channel channel;
    private final JedisPool pool;
    // Don't make this objectMapper a bean. The default bean serializes to camelCase which the extension relies on
    private static final ObjectMapper objectMapper = new ObjectMapper().setPropertyNamingStrategy(
                PropertyNamingStrategy.CAMEL_CASE_TO_LOWER_CASE_WITH_UNDERSCORES)
            .setSerializationInclusion(JsonInclude.Include.NON_NULL);
    private static final JavaType type = objectMapper.getTypeFactory().constructType(SubmissionCacheData.class);


    @Autowired
    public SubmissionController(final ConnectionFactory connectionFactory,
                                final JedisPool jedisPool) throws IOException {
        Connection connection = connectionFactory.newConnection();
        channel = connection.createChannel();
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);
        this.pool = jedisPool;
    }

    @CrossOrigin(origins = "*")
    @RequestMapping(value = "/search", method = RequestMethod.POST)
    public RetrieveSubmissionDataResponse search(final @RequestBody SearchRequest req,
                                                 final HttpServletRequest request) throws IOException {
        final ImmutableMap.Builder<String, List<SubmissionData>> mapBuilder = new ImmutableMap.Builder<>();

        try (Jedis jedis = pool.getResource()) {
            jedis.incr("subredditfinderservices.submissioncontroller.search.ping." + request.getRemoteAddr());
            final List<String> submissions = req.urls.stream().distinct().collect(Collectors.toList());

            submissions.stream()
                       .filter(url -> url != null && !url.isEmpty())
                       .forEach(url -> {
                            try {
                                final String searchDataJson = jedis.get(url);

                                if (searchDataJson == null) {
                                    enqueue(url, jedis);
                                    return;
                                }

                                final SubmissionCacheData cacheData = objectMapper.readValue(searchDataJson, type);

                                if (isPending(cacheData)) {
                                    return;
                                }

                                jedis.incr("subredditfinderservices.submissioncontroller.search.cachehit." + request.getRemoteAddr());
                                log.info("Cache hit: " + url);
                                mapBuilder.put(url, cacheData.getSubmissionDataList());
                            } catch (final Exception exception) {
                                log.error("Failed to process URL " + url, exception);
                            }
                       });

            final Map<String, List<SubmissionData>> map = mapBuilder.build();

            if (submissions.size() == map.size()) {
                jedis.incr("subredditfinderservices.submissioncontroller.search.completepageload." + request.getRemoteAddr());
            }

            return new RetrieveSubmissionDataResponse(map);

        } catch (final Exception exception) {
            log.error("Failed to obtain Jedis pool resource", exception);
            throw exception;
        }
    }

    private void enqueue(final String url, final Jedis jedis) throws IOException {
        try {
            channel.basicPublish("", QUEUE_NAME, null, url.getBytes());
        } catch (final IOException exception) {
            log.error("Failed to publish to queue: '" + url + "'");
            throw exception;
        }

        final SubmissionCacheData pendingSubData = SubmissionCacheData.builder()
                .cacheTimestampUtc(String.valueOf(Instant.now(Clock.systemUTC()).getEpochSecond()))
                .build();

        try {
            jedis.set(url.getBytes(), objectMapper.writeValueAsBytes(pendingSubData), "NX".getBytes(), "EX".getBytes(), 10);
        } catch (final Exception exception) {
            log.error("Failed to create pending data object: '" + url + "'");
        }
    }

    private boolean isPending(final SubmissionCacheData cacheData) {
        return cacheData.getSubmissionDataList() == null;
    }

    @Data
    @AllArgsConstructor
    public static class RetrieveSubmissionDataResponse {
        private Map<String, List<SubmissionData>> submissions;
    }
}
