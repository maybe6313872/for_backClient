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
@Table(name = "email_code")
public class EmailCode {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "email", length = 100, nullable = false)
    private String email = "";

    @Column(name = "code", length = 10, nullable = false)
    private String code = "";

    @Column(name = "created_time", nullable = false)
    private LocalDateTime createdTime;

    @Column(name = "type", length = 10, nullable = false)
    private String type = "test";

    @PrePersist
    void prePersist() {
        if (createdTime == null) {
            createdTime = LocalDateTime.now();
        }
    }
}
