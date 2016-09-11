package com.alexremedios.subredditfinderservice;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SubmissionCacheData {
    String cacheTimestampUtc;
    List<SubmissionData> submissionDataList;
}
