package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.ArtDtos.ArtQueryOutDto;
import com.zhiliao.ainame.dto.OrderDtos.OrderInDto;
import com.zhiliao.ainame.dto.OrderDtos.OrderProductRowOutDto;
import com.zhiliao.ainame.dto.OrderDtos.OrderQueryApiResponseDto;
import com.zhiliao.ainame.dto.OrderDtos.OrderQueryRowOutDto;
import com.zhiliao.ainame.entity.OrderHeader;
import com.zhiliao.ainame.entity.OrderLine;
import com.zhiliao.ainame.repository.CompanyRepository;
import com.zhiliao.ainame.repository.OrderHeaderRepository;
import com.zhiliao.ainame.repository.OrderLineRepository;
import com.zhiliao.ainame.repository.ProductRepository;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import java.util.ArrayList;
import java.util.Map;
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
@RequestMapping("/order")
public class OrderController {
    private final OrderHeaderRepository orders;
    private final OrderLineRepository orderLines;
    private final CompanyRepository companies;
    private final ProductRepository products;

    public OrderController(
        OrderHeaderRepository orders,
        OrderLineRepository orderLines,
        CompanyRepository companies,
        ProductRepository products
    ) {
        this.orders = orders;
        this.orderLines = orderLines;
        this.companies = companies;
        this.products = products;
    }

    @Transactional
    @PostMapping("/create")
    public ArtQueryOutDto create(@Valid @RequestBody OrderInDto data) {
        var order = new OrderHeader();
        order.setOrderNumber(data.orderNumber());
        order.setCompanyId(data.companyId());
        orders.save(order);

        for (var item : data.productList()) {
            var line = new OrderLine();
            line.setOrderId(order.getId());
            line.setProductId(item.id());
            line.setNumber(item.number());
            orderLines.save(line);
        }
        return new ArtQueryOutDto("created successfully");
    }

    @Transactional
    @PutMapping("/update")
    public ResponseEntity<?> update(@Valid @RequestBody OrderInDto data) {
        if (data.id() == null) {
            return ResponseEntity.badRequest().body(Map.of("detail", "缺少订单 id"));
        }
        var order = orders.findById(data.id()).orElse(null);
        if (order == null) {
            return ResponseEntity.badRequest().body(Map.of("detail", "订单不存在"));
        }
        order.setOrderNumber(data.orderNumber());
        order.setCompanyId(data.companyId());
        orders.save(order);

        orderLines.deleteByOrderId(data.id());
        for (var item : data.productList()) {
            var line = new OrderLine();
            line.setOrderId(data.id());
            line.setProductId(item.id());
            line.setNumber(item.number());
            orderLines.save(line);
        }
        return ResponseEntity.ok(new ArtQueryOutDto("updated successfully"));
    }

    @GetMapping("/query")
    public OrderQueryApiResponseDto query() {
        var result = new ArrayList<OrderQueryRowOutDto>();
        for (var order : orders.findAllByOrderByIdAsc()) {
            String companyName = companies.findById(order.getCompanyId()).map(c -> c.getName()).orElse(null);
            var productList = new ArrayList<OrderProductRowOutDto>();
            float total = 0;
            for (var line : orderLines.findByOrderId(order.getId())) {
                var product = products.findById(line.getProductId()).orElse(null);
                float price = product == null || product.getPrice() == null ? 0 : product.getPrice();
                float number = line.getNumber() == null ? 0 : line.getNumber();
                total += price * number;
                productList.add(new OrderProductRowOutDto(
                    line.getProductId(),
                    product == null ? null : product.getName(),
                    line.getNumber(),
                    price
                ));
            }
            result.add(new OrderQueryRowOutDto(
                order.getId(),
                order.getOrderNumber(),
                order.getCompanyId(),
                companyName,
                productList,
                total
            ));
        }
        return new OrderQueryApiResponseDto(result);
    }

    @Transactional
    @DeleteMapping("/delete")
    public ArtQueryOutDto delete(@RequestParam("id") Integer id) {
        orderLines.deleteByOrderId(id);
        orders.deleteById(id);
        return new ArtQueryOutDto("deleted successfully");
    }
}
