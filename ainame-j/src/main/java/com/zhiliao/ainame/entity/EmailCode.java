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
@TableName("email_code")
public class EmailCode implements PersistedEntity {
    @TableId(type = IdType.AUTO)
    private Integer id;

    private String email = "";

    private String code = "";

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdTime;

    private String type = "test";

}
