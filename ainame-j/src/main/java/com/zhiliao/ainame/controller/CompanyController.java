package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.ArtDtos.ArtQueryOutDto;
import com.zhiliao.ainame.dto.OrderDtos.CompanyCreateInDto;
import com.zhiliao.ainame.dto.OrderDtos.CompanyOutDto;
import com.zhiliao.ainame.dto.OrderDtos.CompanyUpdateInDto;
import com.zhiliao.ainame.entity.Company;
import com.zhiliao.ainame.repository.CompanyRepository;
import com.zhiliao.ainame.repository.OrderHeaderRepository;
import com.zhiliao.ainame.repository.OrderLineRepository;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/company")
public class CompanyController {
    private final CompanyRepository companies;
    private final OrderHeaderRepository orders;
    private final OrderLineRepository orderLines;

    public CompanyController(CompanyRepository companies, OrderHeaderRepository orders, OrderLineRepository orderLines) {
        this.companies = companies;
        this.orders = orders;
        this.orderLines = orderLines;
    }

    @PostMapping("/create")
    public ArtQueryOutDto create(@Valid @RequestBody CompanyCreateInDto data) {
        var company = new Company();
        company.setName(data.name());
        company.setAddress(data.address());
        companies.save(company);
        return new ArtQueryOutDto("created successfully");
    }

    @GetMapping("/query")
    public ResponseEntity<?> query() {
        var data = companies.findAllByOrderByIdAsc().stream().map(this::toOut).toList();
        if (data.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "公司未找到"));
        }
        return ResponseEntity.ok(Map.of("code", 200, "message", "查询成功", "data", data));
    }

    @PutMapping("/update")
    public ResponseEntity<?> update(@Valid @RequestBody CompanyUpdateInDto data) {
        var company = companies.findById(data.id()).orElse(null);
        if (company == null) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("detail", "公司不存在"));
        }
        company.setName(data.name());
        company.setAddress(data.address());
        companies.save(company);
        return ResponseEntity.ok(Map.of("code", 200, "message", "更新成功", "data", 1));
    }

    @Transactional
    @DeleteMapping("/delete")
    public Map<String, Object> delete(@RequestParam("company_id") Integer companyId) {
        var company = companies.findById(companyId).orElse(null);
        if (company != null) {
            var orderIds = orders.findByCompanyId(companyId).stream().map(o -> o.getId()).toList();
            if (!orderIds.isEmpty()) {
                orderLines.deleteByOrderIdIn(orderIds);
                orders.deleteByIdIn(orderIds);
            }
            companies.delete(company);
        }
        return Map.of("code", 200, "message", "删除成功", "data", 1);
    }

    private CompanyOutDto toOut(Company company) {
        return new CompanyOutDto(company.getId(), company.getName(), company.getAddress(), company.getCreatedTime());
    }
}
