package com.alexremedios.subredditfinderservice;

import com.codahale.metrics.ConsoleReporter;
import com.codahale.metrics.MetricFilter;
import com.codahale.metrics.MetricRegistry;
import com.codahale.metrics.graphite.Graphite;
import com.codahale.metrics.graphite.GraphiteReporter;
import com.rabbitmq.client.ConnectionFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import java.io.IOException;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.util.Properties;
import java.util.concurrent.TimeUnit;

@Configuration
public class AppConfig {

    private static final JedisPoolConfig config;
    private static final MetricRegistry metrics = new MetricRegistry();
    private final Properties properties;


    static {
        config = new JedisPoolConfig();
        config.setMaxTotal(128);
    }

    private Properties privateConfig;

    public AppConfig() throws IOException {
        properties = getPrivateConfig();
        startGraphiteReporter(properties.getProperty("graphite-ip"));

    }

    private void startGraphiteReporter(final String graphiteIp) {
        final Graphite graphite = new Graphite(new InetSocketAddress(graphiteIp, 2003));
        final GraphiteReporter reporter = GraphiteReporter.forRegistry(metrics)
                .prefixedWith("web1.example.com")
                .convertRatesTo(TimeUnit.SECONDS)
                .convertDurationsTo(TimeUnit.MILLISECONDS)
                .filter(MetricFilter.ALL)
                .build(graphite);
        reporter.start(1, TimeUnit.MINUTES);
    }

    private static void startConsoleReporter() {
        final ConsoleReporter reporter = ConsoleReporter.forRegistry(metrics)
                .convertRatesTo(TimeUnit.SECONDS)
                .convertDurationsTo(TimeUnit.MILLISECONDS)
                .build();
        reporter.start(1, TimeUnit.SECONDS);
    }

    @Bean
    JedisPool jedisPool() {
         return new JedisPool(config, "localhost");
    }

    @Bean
    ConnectionFactory connectionFactory() {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        return factory;
    }

    @Bean
    MetricRegistry metricRegistry() {
        return metrics;
    }

    private Properties getPrivateConfig() throws IOException {
        final Properties props = new Properties();
        final String propFileName = "private-config.properties";

        final InputStream inputStream = getClass().getClassLoader().getResourceAsStream(propFileName);

        if (inputStream != null) {
            props.load(inputStream);
        } else {
            throw new RuntimeException(String.format("Failed to load property file %s", propFileName));
        }

        return props;
    }
}