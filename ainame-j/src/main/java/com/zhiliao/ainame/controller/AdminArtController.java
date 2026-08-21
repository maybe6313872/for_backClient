package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.ArtDtos.ArtChangeIn;
import com.zhiliao.ainame.dto.ArtDtos.ArtDeleteIn;
import com.zhiliao.ainame.dto.ArtDtos.ArtOutDto;
import com.zhiliao.ainame.dto.ArtDtos.ArtQueryIn;
import com.zhiliao.ainame.dto.ArtDtos.ArtQueryOutDto;
import com.zhiliao.ainame.dto.CommonDtos.ResponseOut;
import com.zhiliao.ainame.entity.Art;
import com.zhiliao.ainame.repository.ArtRepository;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/admin")
public class AdminArtController {
    private static final long MAX_THUMBNAIL_BYTES = 100L * 1024 * 1024;

    private final ArtRepository arts;

    public AdminArtController(ArtRepository arts) {
        this.arts = arts;
    }

    @PostMapping(value = "/insertArt", consumes = "multipart/form-data")
    public ResponseEntity<?> insertArt(
        @RequestParam("username") String username,
        @RequestParam("sex") String sex,
        @RequestParam("artcontent") String artcontent,
        @RequestPart("file") MultipartFile file
    ) throws IOException {
        byte[] thumbnail = file.getBytes();
        if (thumbnail.length > MAX_THUMBNAIL_BYTES) {
            return ResponseEntity.status(HttpStatus.PAYLOAD_TOO_LARGE)
                .body(Map.of("detail", "文件大小超过限制，最大允许 100MB"));
        }

        var art = new Art();
        art.setUsername(username);
        art.setSex(sex);
        art.setArtcontent(artcontent);
        art.setThumbnail(thumbnail);
        art.setCreatedTime(LocalDateTime.now());
        arts.save(art);
        return ResponseEntity.ok(new ResponseOut());
    }

    @Transactional
    @PostMapping("/delArt")
    public ResponseEntity<?> delArt(@Valid @RequestBody ArtDeleteIn data) {
        long affected = arts.deleteByIdIn(data.idArr());
        if (affected == 0) {
            return ResponseEntity.badRequest().body(Map.of("detail", "未找到要删除的文章记录"));
        }
        return ResponseEntity.ok(affected);
    }

    @PostMapping("/changeArt")
    public ResponseEntity<?> changeArt(@Valid @RequestBody ArtChangeIn data) {
        var art = arts.findById(data.id()).orElse(null);
        if (art == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "文章不存在"));
        }
        art.setSex(data.sex());
        arts.save(art);
        return ResponseEntity.ok(new ArtQueryOutDto(200, "修改成功", art.getId()));
    }

    @PostMapping("/queryArt")
    public List<ArtOutDto> queryArt(@Valid @RequestBody ArtQueryIn data) {
        return queryArts(data);
    }

    @PostMapping("/queryArtOut")
    public ArtQueryOutDto queryArtOut(@Valid @RequestBody ArtQueryIn data) {
        return new ArtQueryOutDto(queryArts(data));
    }

    List<ArtOutDto> queryArts(ArtQueryIn data) {
        int pageIndex = Math.max(data.pageOrDefault() - 1, 0);
        var pageable = PageRequest.of(pageIndex, data.sizeOrDefault());
        return arts.findBySexOrderByCreatedTimeDesc(data.sex(), pageable).stream()
            .map(this::toOut)
            .toList();
    }

    private ArtOutDto toOut(Art art) {
        return new ArtOutDto(art.getId(), art.getUsername(), art.getSex(), art.getArtcontent());
    }
}
