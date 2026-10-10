package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.EmailCode;
import java.util.Optional;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface EmailCodeRepository extends BaseRepository<EmailCode> {
    default Optional<EmailCode> findFirstByEmailAndCodeOrderByIdDesc(String email, String code) {
        return Optional.ofNullable(selectOne(Wrappers.<EmailCode>query().eq("email", email).eq("code", code).orderByDesc("id").last("LIMIT 1")));
    }
}
