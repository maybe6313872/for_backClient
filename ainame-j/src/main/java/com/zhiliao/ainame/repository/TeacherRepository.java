package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.Teacher;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TeacherRepository extends JpaRepository<Teacher, Integer> {
    List<Teacher> findAllByOrderByIdAsc();

    List<Teacher> findBySchoolIdOrderByIdAsc(Integer schoolId);
}
