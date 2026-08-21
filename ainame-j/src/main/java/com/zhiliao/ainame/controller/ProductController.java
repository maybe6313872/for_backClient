package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.ArtDtos.ArtQueryOutDto;
import com.zhiliao.ainame.dto.OrderDtos.ProductInDto;
import com.zhiliao.ainame.dto.OrderDtos.ProductOutDto;
import com.zhiliao.ainame.entity.Product;
import com.zhiliao.ainame.repository.OrderLineRepository;
import com.zhiliao.ainame.repository.ProductRepository;
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
@RequestMapping("/product")
public class ProductController {
    private final ProductRepository products;
    private final OrderLineRepository orderLines;

    public ProductController(ProductRepository products, OrderLineRepository orderLines) {
        this.products = products;
        this.orderLines = orderLines;
    }

    @PostMapping("/create")
    public ArtQueryOutDto create(@Valid @RequestBody ProductInDto data) {
        var product = new Product();
        fill(product, data);
        products.save(product);
        return new ArtQueryOutDto("created successfully");
    }

    @GetMapping("/query")
    public Map<String, Object> query() {
        var data = products.findAllByOrderByIdAsc().stream().map(this::toOut).toList();
        return Map.of("code", 200, "message", "查询成功", "data", data);
    }

    @PutMapping("/update")
    public ResponseEntity<?> update(@Valid @RequestBody ProductInDto data) {
        if (data.id() == null) {
            return ResponseEntity.badRequest().body(Map.of("detail", "缺少产品 id"));
        }
        var product = products.findById(data.id()).orElse(null);
        if (product == null) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("detail", "产品不存在"));
        }
        fill(product, data);
        products.save(product);
        return ResponseEntity.ok(Map.of("code", 200, "message", "更新成功", "data", 1));
    }

    @Transactional
    @DeleteMapping("/delete")
    public Map<String, Object> delete(@RequestParam("prduct_id") Integer productId) {
        var product = products.findById(productId).orElse(null);
        if (product != null) {
            var orderIds = orderLines.findByProductId(productId).stream().map(l -> l.getOrderId()).distinct().toList();
            for (Integer orderId : orderIds) {
                orderLines.deleteByOrderId(orderId);
            }
            products.delete(product);
        }
        return Map.of("code", 200, "message", "删除成功", "data", 1);
    }

    private void fill(Product product, ProductInDto data) {
        product.setName(data.name());
        product.setPrice(data.price());
        product.setStorenum(data.storenum());
        product.setDescription(data.description());
        product.setProductno(data.productno());
    }

    private ProductOutDto toOut(Product product) {
        return new ProductOutDto(
            product.getId(),
            product.getName(),
            product.getPrice(),
            product.getStorenum(),
            product.getDescription(),
            product.getProductno(),
            product.getCreatedTime()
        );
    }
}
