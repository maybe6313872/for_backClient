package com.zhiliao.ainame.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import java.time.LocalDateTime;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "product")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "name", length = 100, nullable = false)
    private String name = "";

    @Column(name = "price", nullable = false)
    private Float price;

    @Column(name = "storenum", nullable = false)
    private Integer storenum;

    @Column(name = "description", length = 200, nullable = false)
    private String description = "";

    @Column(name = "productno", length = 200, nullable = false)
    private String productno = "";

    @Column(name = "created_time", nullable = false)
    private LocalDateTime createdTime;

    @PrePersist
    void prePersist() {
        if (createdTime == null) {
            createdTime = LocalDateTime.now();
        }
    }
}
