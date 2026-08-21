package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.CommonDtos.ResponseOut;
import com.zhiliao.ainame.dto.SchoolDtos.TeacherInDto;
import com.zhiliao.ainame.dto.SchoolDtos.TeacherListResponseDto;
import com.zhiliao.ainame.dto.SchoolDtos.TeacherOutDto;
import com.zhiliao.ainame.dto.SchoolDtos.TeacherUpdateInDto;
import com.zhiliao.ainame.entity.Teacher;
import com.zhiliao.ainame.repository.StudentCourseRepository;
import com.zhiliao.ainame.repository.StudentRepository;
import com.zhiliao.ainame.repository.TeacherRepository;
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
@RequestMapping("/teacher")
public class TeacherController {
    private final TeacherRepository teachers;
    private final StudentRepository students;
    private final StudentCourseRepository studentCourses;

    public TeacherController(TeacherRepository teachers, StudentRepository students, StudentCourseRepository studentCourses) {
        this.teachers = teachers;
        this.students = students;
        this.studentCourses = studentCourses;
    }

    @PostMapping
    public ResponseOut create(@Valid @RequestBody TeacherInDto data) {
        var teacher = new Teacher();
        teacher.setName(data.name());
        teacher.setSex(data.sex());
        teacher.setAge(data.age());
        teacher.setSchoolId(data.schoolId());
        teachers.save(teacher);
        return new ResponseOut();
    }

    @GetMapping
    public TeacherListResponseDto getAll(@RequestParam(value = "school_id", required = false) Integer schoolId) {
        var list = schoolId == null ? teachers.findAllByOrderByIdAsc() : teachers.findBySchoolIdOrderByIdAsc(schoolId);
        return new TeacherListResponseDto(list.stream().map(this::toOut).toList());
    }

    @GetMapping("/{teacherId}")
    public ResponseEntity<?> getById(@PathVariable("teacherId") Integer teacherId) {
        return teachers.findById(teacherId)
            .<ResponseEntity<?>>map(teacher -> ResponseEntity.ok(toOut(teacher)))
            .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "班主任ID " + teacherId + " 不存在")));
    }

    @PutMapping("/{teacherId}")
    public ResponseEntity<?> update(@PathVariable("teacherId") Integer teacherId, @Valid @RequestBody TeacherUpdateInDto data) {
        var teacher = teachers.findById(teacherId).orElse(null);
        if (teacher == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "班主任ID " + teacherId + " 不存在"));
        }
        if (data.name() != null) teacher.setName(data.name());
        if (data.sex() != null) teacher.setSex(data.sex());
        if (data.age() != null) teacher.setAge(data.age());
        if (data.schoolId() != null) teacher.setSchoolId(data.schoolId());
        teachers.save(teacher);
        return ResponseEntity.ok(new ResponseOut());
    }

    @Transactional
    @DeleteMapping("/{teacherId}")
    public ResponseEntity<?> delete(@PathVariable("teacherId") Integer teacherId) {
        var teacher = teachers.findById(teacherId).orElse(null);
        if (teacher == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "班主任ID " + teacherId + " 不存在"));
        }
        var studentIds = students.findByTeacherIdOrderByIdAsc(teacherId).stream().map(s -> s.getId()).toList();
        if (!studentIds.isEmpty()) {
            studentCourses.deleteByStudentIdIn(studentIds);
        }
        teachers.delete(teacher);
        return ResponseEntity.ok(new ResponseOut());
    }

    private TeacherOutDto toOut(Teacher teacher) {
        return new TeacherOutDto(teacher.getId(), teacher.getName(), teacher.getSex(), teacher.getAge(), teacher.getSchoolId(), teacher.getCreatedTime());
    }
}
