package com.alexremedios.subredditfinderservice;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SubmissionData {
    String subredditName;
    String permalink;
    int score;
    String url;
    String author;
    String createdUtc;
    String title;
}
