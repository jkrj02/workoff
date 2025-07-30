package com.workoff;

import org.springframework.web.bind.annotation.*;
import java.time.*;
import java.util.*;

@RestController
@RequestMapping("/api")
public class WorkTimeController {
    private LocalTime startTime = LocalTime.of(9, 0);
    private LocalTime endTime = LocalTime.of(18, 0);

    @GetMapping("/config")
    public Map<String, String> getConfig() {
        Map<String, String> map = new HashMap<>();
        map.put("start", startTime.toString());
        map.put("end", endTime.toString());
        return map;
    }

    @PostMapping("/config")
    public void setConfig(@RequestBody Map<String, String> config) {
        startTime = LocalTime.parse(config.get("start"));
        endTime = LocalTime.parse(config.get("end"));
    }

    @GetMapping("/time")
    public Map<String, Object> getTime() {
        LocalTime now = LocalTime.now();
        long total = Duration.between(startTime, endTime).toMinutes();
        long passed = Duration.between(startTime, now).toMinutes();
        long left = Duration.between(now, endTime).toMinutes();
        double percent = Math.max(0, Math.min(1, (double)passed / total));
        Map<String, Object> map = new HashMap<>();
        map.put("left", left);
        map.put("percent", percent);
        map.put("now", now.toString());
        return map;
    }
}
 