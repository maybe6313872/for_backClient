package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.CommonDtos.ResponseOut;
import com.zhiliao.ainame.dto.SchoolDtos.CourseWithScoreDto;
import com.zhiliao.ainame.dto.SchoolDtos.StudentInDto;
import com.zhiliao.ainame.dto.SchoolDtos.StudentListResponseDto;
import com.zhiliao.ainame.dto.SchoolDtos.StudentOutDto;
import com.zhiliao.ainame.dto.SchoolDtos.StudentUpdateInDto;
import com.zhiliao.ainame.entity.Student;
import com.zhiliao.ainame.repository.CourseRepository;
import com.zhiliao.ainame.repository.StudentCourseRepository;
import com.zhiliao.ainame.repository.StudentRepository;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import java.util.ArrayList;
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
@RequestMapping("/student")
public class StudentController {
    private final StudentRepository students;
    private final StudentCourseRepository studentCourses;
    private final CourseRepository courses;

    public StudentController(StudentRepository students, StudentCourseRepository studentCourses, CourseRepository courses) {
        this.students = students;
        this.studentCourses = studentCourses;
        this.courses = courses;
    }

    @PostMapping
    public ResponseOut create(@Valid @RequestBody StudentInDto data) {
        var student = new Student();
        student.setName(data.name());
        student.setSex(data.sex());
        student.setAge(data.age());
        student.setTeacherId(data.teacherId());
        students.save(student);
        return new ResponseOut();
    }

    @GetMapping
    public StudentListResponseDto getAll(@RequestParam(value = "teacher_id", required = false) Integer teacherId) {
        var list = teacherId == null ? students.findAllByOrderByIdAsc() : students.findByTeacherIdOrderByIdAsc(teacherId);
        return new StudentListResponseDto(list.stream().map(this::toOut).toList());
    }

    @GetMapping("/{studentId}")
    public ResponseEntity<?> getById(@PathVariable("studentId") Integer studentId) {
        return students.findById(studentId)
            .<ResponseEntity<?>>map(student -> ResponseEntity.ok(toOut(student)))
            .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "学生ID " + studentId + " 不存在")));
    }

    @PutMapping("/{studentId}")
    public ResponseEntity<?> update(@PathVariable("studentId") Integer studentId, @Valid @RequestBody StudentUpdateInDto data) {
        var student = students.findById(studentId).orElse(null);
        if (student == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "学生ID " + studentId + " 不存在"));
        }
        if (data.name() != null) student.setName(data.name());
        if (data.sex() != null) student.setSex(data.sex());
        if (data.age() != null) student.setAge(data.age());
        if (data.teacherId() != null) student.setTeacherId(data.teacherId());
        students.save(student);
        return ResponseEntity.ok(new ResponseOut());
    }

    @Transactional
    @DeleteMapping("/{studentId}")
    public ResponseEntity<?> delete(@PathVariable("studentId") Integer studentId) {
        var student = students.findById(studentId).orElse(null);
        if (student == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "学生ID " + studentId + " 不存在"));
        }
        studentCourses.deleteByStudentId(studentId);
        students.delete(student);
        return ResponseEntity.ok(new ResponseOut());
    }

    private StudentOutDto toOut(Student student) {
        var courseRows = new ArrayList<CourseWithScoreDto>();
        for (var row : studentCourses.findByStudentIdOrderByIdAsc(student.getId())) {
            courses.findById(row.getCourseId())
                .map(CourseController::toOut)
                .ifPresent(course -> courseRows.add(new CourseWithScoreDto(course, row.getScore())));
        }
        return new StudentOutDto(
            student.getId(),
            student.getName(),
            student.getSex(),
            student.getAge(),
            student.getTeacherId(),
            student.getCreatedTime(),
            courseRows
        );
    }
}
