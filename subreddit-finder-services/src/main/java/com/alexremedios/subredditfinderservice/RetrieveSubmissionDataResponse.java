package com.alexremedios.subredditfinderservice;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
@AllArgsConstructor
public class RetrieveSubmissionDataResponse {
    private Map<String, List<SubmissionData>> submissions;
}