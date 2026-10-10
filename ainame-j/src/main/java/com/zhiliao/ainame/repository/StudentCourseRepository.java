package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.StudentCourse;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface StudentCourseRepository extends BaseRepository<StudentCourse> {
    default boolean existsByStudentIdAndCourseId(Integer studentId, Integer courseId) { return selectCount(Wrappers.<StudentCourse>query().eq("student_id", studentId).eq("course_id", courseId)) > 0; }
    default Optional<StudentCourse> findByStudentIdAndCourseId(Integer studentId, Integer courseId) { return Optional.ofNullable(selectOne(Wrappers.<StudentCourse>query().eq("student_id", studentId).eq("course_id", courseId).last("LIMIT 1"))); }
    default List<StudentCourse> findByStudentIdOrderByIdAsc(Integer id) { return selectList(Wrappers.<StudentCourse>query().eq("student_id", id).orderByAsc("id")); }
    default List<StudentCourse> findByCourseIdOrderByIdAsc(Integer id) { return selectList(Wrappers.<StudentCourse>query().eq("course_id", id).orderByAsc("id")); }
    default List<StudentCourse> findAllByOrderByIdAsc() { return selectList(Wrappers.<StudentCourse>query().orderByAsc("id")); }
    default long deleteByStudentId(Integer id) { return delete(Wrappers.<StudentCourse>query().eq("student_id", id)); }
    default long deleteByStudentIdIn(Collection<Integer> ids) { return ids == null || ids.isEmpty() ? 0 : delete(Wrappers.<StudentCourse>query().in("student_id", ids)); }
    default long deleteByCourseId(Integer id) { return delete(Wrappers.<StudentCourse>query().eq("course_id", id)); }
}
