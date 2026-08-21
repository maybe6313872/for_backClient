package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.Course;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CourseRepository extends JpaRepository<Course, Integer> {
    List<Course> findAllByOrderByIdAsc();
}
