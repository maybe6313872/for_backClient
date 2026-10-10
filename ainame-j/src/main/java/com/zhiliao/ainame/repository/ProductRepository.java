package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.Product;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface ProductRepository extends BaseRepository<Product> {
    default List<Product> findAllByOrderByIdAsc() { return selectList(Wrappers.<Product>query().orderByAsc("id")); }
}
