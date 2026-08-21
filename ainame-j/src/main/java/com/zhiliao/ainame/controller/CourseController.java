package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.CommonDtos.ResponseOut;
import com.zhiliao.ainame.dto.SchoolDtos.CourseInDto;
import com.zhiliao.ainame.dto.SchoolDtos.CourseListResponseDto;
import com.zhiliao.ainame.dto.SchoolDtos.CourseOutDto;
import com.zhiliao.ainame.dto.SchoolDtos.CourseUpdateInDto;
import com.zhiliao.ainame.entity.Course;
import com.zhiliao.ainame.repository.CourseRepository;
import com.zhiliao.ainame.repository.StudentCourseRepository;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/course")
public class CourseController {
    private final CourseRepository courses;
    private final StudentCourseRepository studentCourses;

    public CourseController(CourseRepository courses, StudentCourseRepository studentCourses) {
        this.courses = courses;
        this.studentCourses = studentCourses;
    }

    @PostMapping
    public ResponseOut create(@Valid @RequestBody CourseInDto data) {
        var course = new Course();
        course.setName(data.name());
        course.setCredit(data.credit());
        courses.save(course);
        return new ResponseOut();
    }

    @GetMapping
    public CourseListResponseDto getAll() {
        return new CourseListResponseDto(courses.findAllByOrderByIdAsc().stream().map(CourseController::toOut).toList());
    }

    @GetMapping("/{courseId}")
    public ResponseEntity<?> getById(@PathVariable("courseId") Integer courseId) {
        return courses.findById(courseId)
            .<ResponseEntity<?>>map(course -> ResponseEntity.ok(toOut(course)))
            .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "课程ID " + courseId + " 不存在")));
    }

    @PutMapping("/{courseId}")
    public ResponseEntity<?> update(@PathVariable("courseId") Integer courseId, @Valid @RequestBody CourseUpdateInDto data) {
        var course = courses.findById(courseId).orElse(null);
        if (course == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "课程ID " + courseId + " 不存在"));
        }
        if (data.name() != null) course.setName(data.name());
        if (data.credit() != null) course.setCredit(data.credit());
        courses.save(course);
        return ResponseEntity.ok(new ResponseOut());
    }

    @Transactional
    @DeleteMapping("/{courseId}")
    public ResponseEntity<?> delete(@PathVariable("courseId") Integer courseId) {
        var course = courses.findById(courseId).orElse(null);
        if (course == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "课程ID " + courseId + " 不存在"));
        }
        studentCourses.deleteByCourseId(courseId);
        courses.delete(course);
        return ResponseEntity.ok(new ResponseOut());
    }

    public static CourseOutDto toOut(Course course) {
        return new CourseOutDto(course.getId(), course.getName(), course.getCredit(), course.getCreatedTime());
    }
}
