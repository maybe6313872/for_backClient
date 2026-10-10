package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.School;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface SchoolRepository extends BaseRepository<School> {
    default List<School> findAllByOrderByIdAsc() { return selectList(Wrappers.<School>query().orderByAsc("id")); }
}
