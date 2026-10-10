package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.Course;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface CourseRepository extends BaseRepository<Course> {
    default List<Course> findAllByOrderByIdAsc() { return selectList(Wrappers.<Course>query().orderByAsc("id")); }
}
