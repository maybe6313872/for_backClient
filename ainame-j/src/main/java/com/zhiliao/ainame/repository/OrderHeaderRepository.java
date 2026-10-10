package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.OrderHeader;
import java.util.Collection;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface OrderHeaderRepository extends BaseRepository<OrderHeader> {
    default List<OrderHeader> findAllByOrderByIdAsc() { return selectList(Wrappers.<OrderHeader>query().orderByAsc("id")); }
    default List<OrderHeader> findByCompanyId(Integer companyId) { return selectList(Wrappers.<OrderHeader>query().eq("company_id", companyId)); }
    default long deleteByIdIn(Collection<Integer> ids) { return ids == null || ids.isEmpty() ? 0 : delete(Wrappers.<OrderHeader>query().in("id", ids)); }
}
