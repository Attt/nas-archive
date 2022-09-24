package io.github.attt.nasserver;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "io.github.attt.nasserver")
public class NasServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(NasServerApplication.class, args);
    }

}
