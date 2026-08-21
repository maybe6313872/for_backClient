package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.School;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SchoolRepository extends JpaRepository<School, Integer> {
    List<School> findAllByOrderByIdAsc();
}
