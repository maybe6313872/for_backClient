package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.Student;
import java.util.Collection;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface StudentRepository extends BaseRepository<Student> {
    default List<Student> findAllByOrderByIdAsc() { return selectList(Wrappers.<Student>query().orderByAsc("id")); }
    default List<Student> findByTeacherIdOrderByIdAsc(Integer id) { return selectList(Wrappers.<Student>query().eq("teacher_id", id).orderByAsc("id")); }
    default List<Student> findByTeacherIdIn(Collection<Integer> ids) { return ids == null || ids.isEmpty() ? List.of() : selectList(Wrappers.<Student>query().in("teacher_id", ids)); }
    default long deleteByTeacherId(Integer id) { return delete(Wrappers.<Student>query().eq("teacher_id", id)); }
    default long deleteByTeacherIdIn(Collection<Integer> ids) { return ids == null || ids.isEmpty() ? 0 : delete(Wrappers.<Student>query().in("teacher_id", ids)); }
}
