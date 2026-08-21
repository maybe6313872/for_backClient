package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.NameDtos.NameItemDto;
import com.zhiliao.ainame.dto.NameDtos.NameRequest;
import com.zhiliao.ainame.dto.NameDtos.NameResponse;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/name")
public class NameController {
    @PostMapping
    public NameResponse generate(@Valid @RequestBody NameRequest ignored) {
        return new NameResponse(List.of(
            new NameItemDto("张子涵", "《诗经·小雅》", "子：有学问、有德行的人；涵：包容、涵养")
        ));
    }
}
