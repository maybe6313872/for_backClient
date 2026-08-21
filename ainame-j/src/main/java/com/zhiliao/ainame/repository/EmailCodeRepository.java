package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.EmailCode;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface EmailCodeRepository extends JpaRepository<EmailCode, Integer> {
    Optional<EmailCode> findFirstByEmailAndCodeOrderByIdDesc(String email, String code);
}
