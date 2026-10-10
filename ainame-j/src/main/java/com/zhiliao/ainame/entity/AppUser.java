package com.zhiliao.ainame.entity;

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
@TableName("`user`")
public class AppUser implements PersistedEntity {
    @TableId(type = IdType.AUTO)
    private Integer id;

    private String email = "";

    private String username = "";

    @TableField("_password")
    private String passwordHash = "";
}
