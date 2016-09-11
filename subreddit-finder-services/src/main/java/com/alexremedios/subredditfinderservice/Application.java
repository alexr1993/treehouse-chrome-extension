package com.alexremedios.subredditfinderservice;

import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;

@Slf4j
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        System.setProperty("logging.file", "logs/service.log");
        log.info("Starting Application");
        ApplicationContext ctx = SpringApplication.run(Application.class, args);
        log.info("Application Context Created");
    }
}
