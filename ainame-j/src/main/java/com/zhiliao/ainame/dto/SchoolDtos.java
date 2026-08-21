package com.zhiliao.ainame.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDateTime;
import java.util.List;

public final class SchoolDtos {
    private SchoolDtos() {
    }

    public record SchoolInDto(@NotBlank @Size(max = 100) String name, @NotBlank @Size(max = 200) String address) {
    }

    public record SchoolOutDto(Integer id, String name, String address, LocalDateTime createdTime) {
    }

    public record SchoolUpdateInDto(@Size(max = 100) String name, @Size(max = 200) String address) {
    }

    public record SchoolListResponseDto(int code, String message, List<SchoolOutDto> data) {
        public SchoolListResponseDto(List<SchoolOutDto> data) {
            this(200, "查询成功", data);
        }
    }

    public record TeacherInDto(
        @NotBlank @Size(max = 50) String name,
        @NotBlank @Size(max = 10) String sex,
        @Min(0) @Max(150) Integer age,
        @NotNull Integer schoolId
    ) {
    }

    public record TeacherOutDto(Integer id, String name, String sex, Integer age, Integer schoolId, LocalDateTime createdTime) {
    }

    public record TeacherUpdateInDto(@Size(max = 50) String name, @Size(max = 10) String sex, @Min(0) @Max(150) Integer age, Integer schoolId) {
    }

    public record TeacherListResponseDto(int code, String message, List<TeacherOutDto> data) {
        public TeacherListResponseDto(List<TeacherOutDto> data) {
            this(200, "查询成功", data);
        }
    }

    public record CourseInDto(@NotBlank @Size(max = 100) String name, @NotNull Float credit) {
    }

    public record CourseOutDto(Integer id, String name, Float credit, LocalDateTime createdTime) {
    }

    public record CourseUpdateInDto(@Size(max = 100) String name, Float credit) {
    }

    public record CourseListResponseDto(int code, String message, List<CourseOutDto> data) {
        public CourseListResponseDto(List<CourseOutDto> data) {
            this(200, "查询成功", data);
        }
    }

    public record CourseWithScoreDto(CourseOutDto course, Float score) {
    }

    public record StudentInDto(
        @NotBlank @Size(max = 50) String name,
        @NotBlank @Size(max = 10) String sex,
        @Min(0) @Max(150) Integer age,
        @NotNull Integer teacherId
    ) {
    }

    public record StudentOutDto(
        Integer id,
        String name,
        String sex,
        Integer age,
        Integer teacherId,
        LocalDateTime createdTime,
        List<CourseWithScoreDto> courses
    ) {
    }

    public record StudentUpdateInDto(@Size(max = 50) String name, @Size(max = 10) String sex, @Min(0) @Max(150) Integer age, Integer teacherId) {
    }

    public record StudentListResponseDto(int code, String message, List<StudentOutDto> data) {
        public StudentListResponseDto(List<StudentOutDto> data) {
            this(200, "查询成功", data);
        }
    }

    public record StudentCourseInDto(@NotNull Integer studentId, @NotNull Integer courseId, @DecimalMin("0.0") @DecimalMax("100.0") Float score) {
    }

    public record StudentCourseOutDto(Integer id, Integer studentId, Integer courseId, Float score, LocalDateTime createdTime) {
    }

    public record StudentCourseUpdateInDto(@DecimalMin("0.0") @DecimalMax("100.0") Float score) {
    }

    public record StudentCourseBatchInDto(@NotNull Integer studentId, @NotEmpty List<Integer> courseIds, List<Float> scores) {
    }

    public record StudentWithScoreDto(Integer studentId, String studentName, String studentSex, Integer studentAge, Integer teacherId, Float score) {
    }

    public record StudentCourseListResponseDto(int code, String message, List<StudentCourseOutDto> data) {
        public StudentCourseListResponseDto(List<StudentCourseOutDto> data) {
            this(200, "查询成功", data);
        }
    }

    public record StudentsByCourseResponseDto(int code, String message, List<StudentWithScoreDto> data) {
        public StudentsByCourseResponseDto(List<StudentWithScoreDto> data) {
            this(200, "查询成功", data);
        }
    }
}
