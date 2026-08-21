package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.StudentCourse;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StudentCourseRepository extends JpaRepository<StudentCourse, Integer> {
    boolean existsByStudentIdAndCourseId(Integer studentId, Integer courseId);

    Optional<StudentCourse> findByStudentIdAndCourseId(Integer studentId, Integer courseId);

    List<StudentCourse> findByStudentIdOrderByIdAsc(Integer studentId);

    List<StudentCourse> findByCourseIdOrderByIdAsc(Integer courseId);

    List<StudentCourse> findAllByOrderByIdAsc();

    long deleteByStudentId(Integer studentId);

    long deleteByStudentIdIn(Collection<Integer> studentIds);

    long deleteByCourseId(Integer courseId);
}
