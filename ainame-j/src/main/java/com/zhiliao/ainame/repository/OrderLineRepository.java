package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.OrderLine;
import java.util.Collection;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface OrderLineRepository extends BaseRepository<OrderLine> {
    default List<OrderLine> findByOrderId(Integer id) { return selectList(Wrappers.<OrderLine>query().eq("order_id", id)); }
    default List<OrderLine> findByProductId(Integer id) { return selectList(Wrappers.<OrderLine>query().eq("product_id", id)); }
    default long deleteByOrderId(Integer id) { return delete(Wrappers.<OrderLine>query().eq("order_id", id)); }
    default long deleteByOrderIdIn(Collection<Integer> ids) { return ids == null || ids.isEmpty() ? 0 : delete(Wrappers.<OrderLine>query().in("order_id", ids)); }
}
