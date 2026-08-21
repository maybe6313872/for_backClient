package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.OrderLine;
import java.util.Collection;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderLineRepository extends JpaRepository<OrderLine, Integer> {
    List<OrderLine> findByOrderId(Integer orderId);

    List<OrderLine> findByProductId(Integer productId);

    long deleteByOrderId(Integer orderId);

    long deleteByOrderIdIn(Collection<Integer> orderIds);
}
