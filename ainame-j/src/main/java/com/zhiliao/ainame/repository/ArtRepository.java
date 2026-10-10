package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.Art;
import java.util.Collection;
import java.util.List;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface ArtRepository extends BaseRepository<Art> {
    @Insert("""
        INSERT INTO art (username, sex, artcontent, thumbnail, created_time)
        VALUES (#{username}, #{sex}, #{artcontent}, #{thumbnail}, #{createdTime})
        """)
    @Options(useGeneratedKeys = true, keyProperty = "id", keyColumn = "id")
    int insertArt(Art art);

    @Delete("""
        <script>
        DELETE FROM art WHERE id IN
        <foreach collection='ids' item='id' open='(' separator=',' close=')'>
            #{id}
        </foreach>
        </script>
        """)
    int deleteByIdIn(@Param("ids") Collection<Integer> ids);

    @Select("""
        SELECT id, username, sex, artcontent, thumbnail, created_time
        FROM art
        WHERE id = #{id}
        """)
    Art findArtById(@Param("id") Integer id);

    @Update("UPDATE art SET sex = #{sex} WHERE id = #{id}")
    int updateSexById(@Param("id") Integer id, @Param("sex") String sex);

    @Select("""
        SELECT id, username, sex, artcontent, thumbnail, created_time
        FROM art
        WHERE sex = #{sex}
        ORDER BY created_time DESC
        LIMIT #{offset}, #{size}
        """)
    List<Art> findBySexOrderByCreatedTimeDesc(
        @Param("sex") String sex,
        @Param("offset") int offset,
        @Param("size") int size
    );
}
