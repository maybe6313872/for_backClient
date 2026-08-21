package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.OrderHeader;
import java.util.Collection;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderHeaderRepository extends JpaRepository<OrderHeader, Integer> {
    List<OrderHeader> findAllByOrderByIdAsc();

    List<OrderHeader> findByCompanyId(Integer companyId);

    long deleteByIdIn(Collection<Integer> ids);
}
