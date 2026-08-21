package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.Company;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CompanyRepository extends JpaRepository<Company, Integer> {
    List<Company> findAllByOrderByIdAsc();
}
