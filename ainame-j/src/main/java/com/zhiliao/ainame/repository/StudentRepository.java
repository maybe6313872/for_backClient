package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.Student;
import java.util.Collection;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StudentRepository extends JpaRepository<Student, Integer> {
    List<Student> findAllByOrderByIdAsc();

    List<Student> findByTeacherIdOrderByIdAsc(Integer teacherId);

    List<Student> findByTeacherIdIn(Collection<Integer> teacherIds);
}
