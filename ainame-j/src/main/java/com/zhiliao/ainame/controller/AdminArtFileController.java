package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.ArtDtos.ArtQueryIn;
import com.zhiliao.ainame.dto.CommonDtos.ResponseOut;
import com.zhiliao.ainame.entity.Art;
import com.zhiliao.ainame.repository.ArtRepository;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.DataFormatter;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.WorkbookFactory;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
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
public class AdminArtFileController {
    private final ArtRepository arts;

    public AdminArtFileController(ArtRepository arts) {
        this.arts = arts;
    }

    @PostMapping("/queryArtExcel")
    public ResponseEntity<byte[]> queryArtExcel(@Valid @RequestBody ArtQueryIn data) throws IOException {
        int pageIndex = Math.max(data.pageOrDefault() - 1, 0);
        var items = arts.findBySexOrderByCreatedTimeDesc(data.sex(), PageRequest.of(pageIndex, data.sizeOrDefault()));

        try (var wb = new XSSFWorkbook(); var out = new ByteArrayOutputStream()) {
            var sheet = wb.createSheet("文章列表");
            Row header = sheet.createRow(0);
            header.createCell(0).setCellValue("ID");
            header.createCell(1).setCellValue("用户名");
            header.createCell(2).setCellValue("性别");
            header.createCell(3).setCellValue("文章内容");

            for (int i = 0; i < items.size(); i++) {
                Art art = items.get(i);
                Row row = sheet.createRow(i + 1);
                row.createCell(0).setCellValue(art.getId());
                row.createCell(1).setCellValue(art.getUsername());
                row.createCell(2).setCellValue(art.getSex());
                row.createCell(3).setCellValue(art.getArtcontent());
            }

            for (int i = 0; i < 4; i++) {
                sheet.autoSizeColumn(i);
            }

            wb.write(out);
            String timestamp = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss").format(LocalDateTime.now());
            String filename = "文章列表_" + timestamp + ".xlsx";
            String encoded = URLEncoder.encode(filename, StandardCharsets.UTF_8).replace("+", "%20");
            return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"article_list_" + timestamp + ".xlsx\"; filename*=UTF-8''" + encoded)
                .contentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .body(out.toByteArray());
        }
    }

    @Transactional
    @PostMapping(value = "/insertArtByExcel", consumes = "multipart/form-data")
    public ResponseEntity<?> insertArtByExcel(@RequestPart("file") MultipartFile file, @RequestParam(value = "username", required = false) String username) throws IOException {
        String filename = file.getOriginalFilename() == null ? "" : file.getOriginalFilename();
        if (!filename.toLowerCase().endsWith(".xlsx") && !filename.toLowerCase().endsWith(".xls")) {
            return ResponseEntity.badRequest().body(Map.of("detail", "文件格式错误，仅支持 .xlsx 或 .xls 格式"));
        }

        ParsedSheet sheet;
        try {
            sheet = parseExcel(file.getBytes());
        } catch (Exception ex) {
            return ResponseEntity.badRequest().body(Map.of("detail", ex.getMessage()));
        }
        if (sheet.rows().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("detail", "Excel文件为空或没有数据行"));
        }

        int colUser = findColumn(sheet.headers(), "用户名", "username", "用户");
        int colSex = findColumn(sheet.headers(), "性别", "sex");
        int colContent = findColumn(sheet.headers(), "文章内容", "artcontent", "内容", "content");
        int colThumb = findColumn(sheet.headers(), "缩略图", "thumbnail", "图片", "image");
        if (colUser < 0) return ResponseEntity.badRequest().body(Map.of("detail", "Excel文件中缺少'用户名'列"));
        if (colSex < 0) return ResponseEntity.badRequest().body(Map.of("detail", "Excel文件中缺少'性别'列"));
        if (colContent < 0) return ResponseEntity.badRequest().body(Map.of("detail", "Excel文件中缺少'文章内容'列"));

        List<String> errors = new ArrayList<>();
        int success = 0;
        int rowNum = 2;
        for (Map<Integer, String> row : sheet.rows()) {
            String u = row.get(colUser);
            String s = row.get(colSex);
            String c = row.get(colContent);
            String th = colThumb >= 0 ? row.get(colThumb) : null;

            if (isBlank(u) || isBlank(s) || isBlank(c)) {
                errors.add("第" + rowNum + "行：缺少必需字段（用户名、性别、文章内容）");
                rowNum++;
                continue;
            }
            u = u.trim();
            s = s.trim();
            c = c.trim();
            if (u.length() > 100) { errors.add("第" + rowNum + "行：用户名长度超过100字符"); rowNum++; continue; }
            if (s.length() > 10) { errors.add("第" + rowNum + "行：性别长度超过10字符"); rowNum++; continue; }
            if (c.length() > 5000) { errors.add("第" + rowNum + "行：文章内容长度超过5000字符"); rowNum++; continue; }

            byte[] thumbBytes = new byte[0];
            if (!isBlank(th)) {
                try {
                    thumbBytes = Base64.getDecoder().decode(th.trim());
                } catch (IllegalArgumentException ex) {
                    errors.add("第" + rowNum + "行：缩略图base64解码失败，将使用空缩略图");
                }
            }

            var art = new Art();
            art.setUsername(u);
            art.setSex(s);
            art.setArtcontent(c);
            art.setThumbnail(thumbBytes);
            art.setCreatedTime(LocalDateTime.now());
            arts.save(art);
            success++;
            rowNum++;
        }

        if (success == 0) {
            String msg = "批量导入失败，共" + errors.size() + "条错误。";
            if (!errors.isEmpty()) {
                msg += " 前5条错误：" + String.join("; ", errors.stream().limit(5).toList());
            }
            return ResponseEntity.badRequest().body(Map.of("detail", msg));
        }
        return ResponseEntity.ok(new ResponseOut());
    }

    private ParsedSheet parseExcel(byte[] content) throws IOException {
        try (var wb = WorkbookFactory.create(new ByteArrayInputStream(content))) {
            var sheet = wb.getSheetAt(0);
            if (sheet == null || sheet.getPhysicalNumberOfRows() == 0) {
                throw new IllegalArgumentException("工作表为空");
            }
            var formatter = new DataFormatter();
            Row headerRow = sheet.getRow(0);
            var headers = new ArrayList<String>();
            for (Cell cell : headerRow) {
                headers.add(formatter.formatCellValue(cell).trim());
            }

            var rows = new ArrayList<Map<Integer, String>>();
            for (int r = 1; r <= sheet.getLastRowNum(); r++) {
                Row row = sheet.getRow(r);
                if (row == null) continue;
                Map<Integer, String> values = new HashMap<>();
                boolean allBlank = true;
                for (int c = 0; c < headers.size(); c++) {
                    String value = formatter.formatCellValue(row.getCell(c));
                    if (!isBlank(value)) {
                        allBlank = false;
                        values.put(c, value);
                    }
                }
                if (!allBlank) {
                    rows.add(values);
                }
            }
            return new ParsedSheet(headers, rows);
        }
    }

    private int findColumn(List<String> headers, String... aliases) {
        for (int i = 0; i < headers.size(); i++) {
            for (String alias : aliases) {
                if (headers.get(i).equalsIgnoreCase(alias)) {
                    return i;
                }
            }
        }
        return -1;
    }

    private boolean isBlank(String value) {
        return value == null || value.isBlank();
    }

    private record ParsedSheet(List<String> headers, List<Map<Integer, String>> rows) {
    }
}
