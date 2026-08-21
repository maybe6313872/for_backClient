package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.AppUser;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AppUserRepository extends JpaRepository<AppUser, Integer> {
    boolean existsByEmail(String email);

    Optional<AppUser> findByEmail(String email);
}
