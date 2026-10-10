package com.zhiliao.ainame.entity;

import java.time.LocalDateTime;
import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@TableName("student")
public class Student implements PersistedEntity {
    @TableId(type = IdType.AUTO)
    private Integer id;

    private String name = "";

    private String sex = "";

    private Integer age;

    private Integer teacherId;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdTime;

    @TableField(exist = false)
    private Teacher teacher;

}
