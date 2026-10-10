package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.Teacher;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface TeacherRepository extends BaseRepository<Teacher> {
    default List<Teacher> findAllByOrderByIdAsc() { return selectList(Wrappers.<Teacher>query().orderByAsc("id")); }
    default List<Teacher> findBySchoolIdOrderByIdAsc(Integer id) { return selectList(Wrappers.<Teacher>query().eq("school_id", id).orderByAsc("id")); }
    default long deleteBySchoolId(Integer id) { return delete(Wrappers.<Teacher>query().eq("school_id", id)); }
}
