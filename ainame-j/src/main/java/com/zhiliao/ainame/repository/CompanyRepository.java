package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.Company;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface CompanyRepository extends BaseRepository<Company> {
    default List<Company> findAllByOrderByIdAsc() { return selectList(Wrappers.<Company>query().orderByAsc("id")); }
}
