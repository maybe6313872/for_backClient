package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.CommonDtos.ResponseOut;
import com.zhiliao.ainame.dto.SchoolDtos.StudentCourseBatchInDto;
import com.zhiliao.ainame.dto.SchoolDtos.StudentCourseInDto;
import com.zhiliao.ainame.dto.SchoolDtos.StudentCourseListResponseDto;
import com.zhiliao.ainame.dto.SchoolDtos.StudentCourseOutDto;
import com.zhiliao.ainame.dto.SchoolDtos.StudentCourseUpdateInDto;
import com.zhiliao.ainame.dto.SchoolDtos.StudentWithScoreDto;
import com.zhiliao.ainame.dto.SchoolDtos.StudentsByCourseResponseDto;
import com.zhiliao.ainame.entity.StudentCourse;
import com.zhiliao.ainame.repository.StudentCourseRepository;
import com.zhiliao.ainame.repository.StudentRepository;
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
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/student-course")
public class StudentCourseController {
    private final StudentCourseRepository studentCourses;
    private final StudentRepository students;

    public StudentCourseController(StudentCourseRepository studentCourses, StudentRepository students) {
        this.studentCourses = studentCourses;
        this.students = students;
    }

    @Transactional
    @PostMapping
    public ResponseEntity<?> batchReplace(@Valid @RequestBody StudentCourseBatchInDto data) {
        if (data.scores() != null && data.scores().size() != data.courseIds().size()) {
            return ResponseEntity.badRequest().body(Map.of("detail", "分数数组长度必须与课程ID数组长度一致"));
        }
        studentCourses.deleteByStudentId(data.studentId());
        for (int i = 0; i < data.courseIds().size(); i++) {
            var row = new StudentCourse();
            row.setStudentId(data.studentId());
            row.setCourseId(data.courseIds().get(i));
            row.setScore(data.scores() == null ? null : data.scores().get(i));
            studentCourses.save(row);
        }
        return ResponseEntity.ok(new ResponseOut());
    }

    @PostMapping("/single")
    public ResponseEntity<?> createSingle(@Valid @RequestBody StudentCourseInDto data) {
        if (studentCourses.existsByStudentIdAndCourseId(data.studentId(), data.courseId())) {
            return ResponseEntity.badRequest().body(Map.of("detail", "该学生已选修此课程"));
        }
        var row = new StudentCourse();
        row.setStudentId(data.studentId());
        row.setCourseId(data.courseId());
        row.setScore(data.score());
        studentCourses.save(row);
        return ResponseEntity.ok(new ResponseOut());
    }

    @GetMapping("/course/{courseId}/students")
    public StudentsByCourseResponseDto getStudentsByCourse(@PathVariable("courseId") Integer courseId) {
        var data = studentCourses.findByCourseIdOrderByIdAsc(courseId).stream()
            .flatMap(row -> students.findById(row.getStudentId()).stream()
                .map(student -> new StudentWithScoreDto(
                    student.getId(),
                    student.getName(),
                    student.getSex(),
                    student.getAge(),
                    student.getTeacherId(),
                    row.getScore()
                )))
            .toList();
        return new StudentsByCourseResponseDto(data);
    }

    @GetMapping
    public StudentCourseListResponseDto getAll(
        @RequestParam(value = "student_id", required = false) Integer studentId,
        @RequestParam(value = "course_id", required = false) Integer courseId
    ) {
        var list = studentId != null
            ? studentCourses.findByStudentIdOrderByIdAsc(studentId)
            : courseId != null
                ? studentCourses.findByCourseIdOrderByIdAsc(courseId)
                : studentCourses.findAllByOrderByIdAsc();
        return new StudentCourseListResponseDto(list.stream().map(this::toOut).toList());
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getById(@PathVariable("id") Integer id) {
        return studentCourses.findById(id)
            .<ResponseEntity<?>>map(row -> ResponseEntity.ok(toOut(row)))
            .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "关联记录ID " + id + " 不存在")));
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> update(@PathVariable("id") Integer id, @Valid @RequestBody StudentCourseUpdateInDto data) {
        var row = studentCourses.findById(id).orElse(null);
        if (row == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "关联记录ID " + id + " 不存在"));
        }
        if (data.score() != null) row.setScore(data.score());
        studentCourses.save(row);
        return ResponseEntity.ok(new ResponseOut());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> delete(@PathVariable("id") Integer id) {
        var row = studentCourses.findById(id).orElse(null);
        if (row == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "关联记录ID " + id + " 不存在"));
        }
        studentCourses.delete(row);
        return ResponseEntity.ok(new ResponseOut());
    }

    private StudentCourseOutDto toOut(StudentCourse row) {
        return new StudentCourseOutDto(row.getId(), row.getStudentId(), row.getCourseId(), row.getScore(), row.getCreatedTime());
    }
}
