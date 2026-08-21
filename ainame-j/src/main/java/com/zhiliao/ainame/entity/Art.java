package com.zhiliao.ainame.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
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
@Table(name = "art")
public class Art {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "username", length = 100, nullable = false)
    private String username = "";

    @Column(name = "sex", length = 10, nullable = false)
    private String sex = "";

    @Column(name = "artcontent", length = 5000, nullable = false)
    private String artcontent = "";

    @Lob
    @Column(name = "thumbnail", columnDefinition = "LONGBLOB", nullable = false)
    private byte[] thumbnail = new byte[0];

    @Column(name = "created_time", nullable = false)
    private LocalDateTime createdTime;

    @PrePersist
    void prePersist() {
        if (createdTime == null) {
            createdTime = LocalDateTime.now();
        }
    }
}
