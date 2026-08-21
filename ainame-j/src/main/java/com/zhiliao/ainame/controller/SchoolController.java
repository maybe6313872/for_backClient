package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.CommonDtos.ResponseOut;
import com.zhiliao.ainame.dto.SchoolDtos.SchoolInDto;
import com.zhiliao.ainame.dto.SchoolDtos.SchoolListResponseDto;
import com.zhiliao.ainame.dto.SchoolDtos.SchoolOutDto;
import com.zhiliao.ainame.dto.SchoolDtos.SchoolUpdateInDto;
import com.zhiliao.ainame.entity.School;
import com.zhiliao.ainame.repository.SchoolRepository;
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
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/school")
public class SchoolController {
    private final SchoolRepository schools;
    private final TeacherRepository teachers;
    private final StudentRepository students;
    private final StudentCourseRepository studentCourses;

    public SchoolController(SchoolRepository schools, TeacherRepository teachers, StudentRepository students, StudentCourseRepository studentCourses) {
        this.schools = schools;
        this.teachers = teachers;
        this.students = students;
        this.studentCourses = studentCourses;
    }

    @PostMapping
    public ResponseOut create(@Valid @RequestBody SchoolInDto data) {
        var school = new School();
        school.setName(data.name());
        school.setAddress(data.address());
        schools.save(school);
        return new ResponseOut();
    }

    @GetMapping
    public SchoolListResponseDto getAll() {
        return new SchoolListResponseDto(schools.findAllByOrderByIdAsc().stream().map(this::toOut).toList());
    }

    @GetMapping("/{schoolId}")
    public ResponseEntity<?> getById(@PathVariable("schoolId") Integer schoolId) {
        return schools.findById(schoolId)
            .<ResponseEntity<?>>map(school -> ResponseEntity.ok(toOut(school)))
            .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "学校ID " + schoolId + " 不存在")));
    }

    @PutMapping("/{schoolId}")
    public ResponseEntity<?> update(@PathVariable("schoolId") Integer schoolId, @Valid @RequestBody SchoolUpdateInDto data) {
        var school = schools.findById(schoolId).orElse(null);
        if (school == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "学校ID " + schoolId + " 不存在"));
        }
        if (data.name() != null) school.setName(data.name());
        if (data.address() != null) school.setAddress(data.address());
        schools.save(school);
        return ResponseEntity.ok(new ResponseOut());
    }

    @Transactional
    @DeleteMapping("/{schoolId}")
    public ResponseEntity<?> delete(@PathVariable("schoolId") Integer schoolId) {
        var school = schools.findById(schoolId).orElse(null);
        if (school == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "学校ID " + schoolId + " 不存在"));
        }
        var teacherIds = teachers.findBySchoolIdOrderByIdAsc(schoolId).stream().map(t -> t.getId()).toList();
        if (!teacherIds.isEmpty()) {
            var studentIds = students.findByTeacherIdIn(teacherIds).stream().map(s -> s.getId()).toList();
            if (!studentIds.isEmpty()) {
                studentCourses.deleteByStudentIdIn(studentIds);
            }
        }
        schools.delete(school);
        return ResponseEntity.ok(new ResponseOut());
    }

    private SchoolOutDto toOut(School school) {
        return new SchoolOutDto(school.getId(), school.getName(), school.getAddress(), school.getCreatedTime());
    }
}
