# Java 语法学习指南（面向 JavaScript / TypeScript 开发者）

本文基于 Java 21，目标是帮助有 JavaScript 或 TypeScript 经验的前端开发者读懂并写出 Java 后端代码。它重点解释常用语法、背后的思维差异，以及你在 Spring Boot 项目中马上会遇到的写法。

## 1. 先建立 Java 的运行模型

Java 是静态类型、编译型、面向对象语言。

```text
Java 源码（.java） -> javac 编译器 -> 字节码（.class） -> JVM 执行
```

可以先把它理解为：Java 是一门比 TypeScript 更严格，并且真正编译后交给 JVM 运行的语言。

| Java | JavaScript / TypeScript |
| --- | --- |
| 类型由编译器强制检查 | JS 检查较少，TS 主要在构建时检查 |
| 通常一个公开类一个文件 | 一个模块可导出多个值 |
| 运行在 JVM | 运行在浏览器或 Node.js |
| `null` 是常见运行时风险 | `null` 与 `undefined` 都很常见 |
| 字段和方法有明确访问权限 | 更多依靠模块边界与约定 |

Java 代码比 JS 多一些声明，但类型、依赖和边界会更明确，因此大型项目更容易被 IDE、编译器和团队成员理解。

## 2. 程序入口 `main`

普通 Java 程序从 `main` 方法启动：

```java
package com.example.ainame;

public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, Java");
    }
}
```

它的固定形态是：

```java
public static void main(String[] args)
```

- `public`：JVM 能从外部访问该方法。
- `static`：不用先 `new Main()`，就能调用该方法。
- `void`：没有返回值。
- `String[] args`：命令行参数数组。

Spring Boot 项目也从这里启动，只是里面通常调用 `SpringApplication.run(...)`。之后 Spring 会启动 Web 服务，并自动创建和组装应用需要的对象。

## 3. 文件、包、导入

一个 Java 文件常见的结构如下：

```java
package com.example.ainame.user;

import java.time.Instant;
import java.util.List;

public class UserService {
}
```

- `package`：类的命名空间与目录身份，可近似理解为项目内模块路径。
- `import`：让其他类的短名称可用，类似 JS 的 `import`，但 Java 这里主要导入“类型”。
- `public class UserService`：声明一个公开类。公开顶层类必须与文件同名，即文件必须叫 `UserService.java`。

例如，导入 `java.util.List` 后，就可直接写 `List`，不需要每次都写 `java.util.List`。

### 同名类冲突

如果两个包里都有同名类，导入一个，另一个使用完整包名：

```java
import java.util.Date;

Date legacyDate = new Date();
java.sql.Date sqlDate = new java.sql.Date(System.currentTimeMillis());
```

Java 不支持 TypeScript 的 `import { User as AuthUser }` 这种导入别名写法。遇到冲突时，用完整类名即可。

## 4. 变量与基础类型

Java 的局部变量必须显式指定类型，或者让 `var` 从初始值推导：

```java
String name = "Ada";
int age = 28;
boolean active = true;
double score = 98.5;
char grade = 'A';

var greeting = "Hello"; // 编译器推导为 String
```

这里的 `var` 不等于 JavaScript 的 `var`。Java 的 `var` 只能用于有明确初始值的局部变量，不能用于字段、参数，也不能只赋值 `null`：

```java
var user = new User("Ada"); // 合法
// var empty = null;         // 不合法，编译器无法判断类型
```

### 基本类型与引用类型

| 分类 | 类型 | 可粗略类比 JS |
| --- | --- | --- |
| 基本类型 | `byte`、`short`、`int`、`long`、`float`、`double`、`boolean`、`char` | 数字、布尔、单字符 |
| 引用类型 | `String`、数组、类、接口、集合 | 对象和数组 |

基本类型直接保存简单值；引用类型变量保存对象引用，因此可以为 `null`。

```java
int count = 3;
Integer optionalCount = null; // 包装类型，可为空
String title = null;
```

`Integer`、`Boolean` 等是基本类型的包装类。泛型只能接收引用类型，所以 `List<Integer>` 合法，`List<int>` 不合法。

### 常量与 `final`

```java
final String apiVersion = "v1";
final User user = new User("Ada");
```

`final` 表示变量赋值后不能重新指向另一个值，接近 JS 的 `const`。但是它不代表对象完全不可变：

```java
final List<String> tags = new ArrayList<>();
tags.add("java"); // 合法，修改的是列表内容
// tags = new ArrayList<>(); // 不合法，不能重新赋值变量
```

类级别常量通常写为：

```java
public static final int MAX_PAGE_SIZE = 100;
```

## 5. 字符串、数字与运算符

```java
String fullName = firstName + " " + lastName;
int total = price * quantity;
double average = (double) total / count;
boolean allowed = age >= 18 && active;
```

常用运算符与 JS 基本一致：

```text
+  -  *  /  %
==  !=  >  >=  <  <=
&&  ||  !
=  -=  *=  /=
```

### `==` 与 `.equals()`：Java 最容易踩的坑之一

对基本类型，`==` 比较数值；对对象，`==` 比较是否指向同一个对象。

```java
String first = new String("hello");
String second = new String("hello");

System.out.println(first == second);      // false：不是同一个对象
System.out.println(first.equals(second)); // true：内容相同
```

比较字符串、`Long`、DTO 等对象内容时，通常使用 `.equals(...)`。如果左侧可能为 `null`，把确定非空的值放在左侧：

```java
boolean isAdmin = "ADMIN".equals(role);
```

枚举使用 `==` 是正确的，因为每个枚举值都是唯一实例。

### 类型转换

```java
int value = 10;
double result = (double) value / 3;

String text = "42";
int number = Integer.parseInt(text);
String output = String.valueOf(number);
```

小心整数除法：`10 / 3` 的结果是 `3`，不是 `3.333`。只要一侧转成 `double`，结果才会保留小数。

## 6. 条件判断与 `switch`

```java
if (score >= 90) {
    grade = "A";
} else if (score >= 60) {
    grade = "及格";
} else {
    grade = "不及格";
}
```

Java 条件表达式必须是 `boolean`，不像 JavaScript 有“真值/假值”转换：

```java
// if (name) { } // 不合法
if (name != null && !name.isBlank()) {
    System.out.println(name);
}
```

### 三元表达式

```java
String label = active ? "已启用" : "已禁用";
```

### Java 21 的 `switch` 表达式

现代 Java 推荐使用带箭头的 `switch`：

```java
String message = switch (status) {
    case "PENDING" -> "等待中";
    case "DONE" -> "已完成";
    default -> "未知状态";
};
```

多行分支使用 `yield` 返回值：

```java
int fee = switch (level) {
    case "VIP" -> 0;
    case "STANDARD" -> {
        int baseFee = 10;
        yield baseFee;
    }
    default -> 20;
};
```

旧写法会在 `case` 后使用 `break`，新写法更不容易发生分支穿透（fall-through），在新项目中优先掌握箭头写法。

## 7. 循环

```java
for (int index = 0; index < 3; index++) {
    System.out.println(index);
}

int index = 0;
while (index < 3) {
    index++;
}
```

遍历集合时，增强 `for` 循环最常用：

```java
for (String tag : tags) {
    System.out.println(tag);
}
```

它接近 JS 的：

```typescript
for (const tag of tags) {
  console.log(tag);
}
```

`break` 退出循环或 `switch`；`continue` 跳过当前循环，进入下一轮。

## 8. 方法

方法就是定义在类、记录、枚举或接口内部的函数：

```java
public String formatName(String firstName, String lastName) {
    return firstName + " " + lastName;
}
```

方法的一般结构：

```text
访问权限 [static] 返回类型 方法名(参数类型 参数名)
```

```java
private static int add(int left, int right) {
    return left + right;
}
```

Java 支持方法重载，即同一个方法名可以根据参数类型或数量不同而有多个版本：

```java
public void log(String message) {
}

public void log(String message, Throwable error) {
}
```

Java 不支持 TypeScript 那样的可选参数、命名参数。常见替代方案是重载、Builder 模式，或传一个配置对象。

### 参数传递：始终是值传递

Java 总是值传递。对象参数传递的是“对象引用的副本”：

```java
void rename(User user) {
    user.setName("Grace"); // 修改同一个 User 对象
}

void replace(User user) {
    user = new User("Grace"); // 只改变当前方法内的变量
}
```

这点和 JS 中把对象传入函数后的感受类似，但理解“引用本身也被复制”能避免很多误判。

## 9. 类、对象与构造器

```java
public class User {
    private String name;
    private int age;

    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public boolean isAdult() {
        return age >= 18;
    }
}

User user = new User("Ada", 28);
System.out.println(user.getName());
```

| Java | TypeScript 类比 |
| --- | --- |
| `class User` | `class User` |
| `new User(...)` | `new User(...)` |
| 与类同名的构造器 | `constructor(...)` |
| `this.name` | `this.name` |
| `private` 字段 | `private` 字段 |
| Getter / Setter | 访问器或公开字段约定 |

`this.name = name` 中，`this.name` 是对象字段，右侧 `name` 是构造器参数。

### 访问修饰符

| 修饰符 | 可访问范围 |
| --- | --- |
| `public` | 任意位置 |
| `protected` | 同包类和子类 |
| 不写修饰符 | 仅同一个包 |
| `private` | 仅当前类 |

不写修饰符的情况叫“包私有”（package-private）。Java 的包不仅用于分类，也是一层实际的访问边界。

## 10. `static` 与实例成员

实例字段和实例方法属于某一个对象：

```java
User user = new User("Ada", 28);
boolean adult = user.isAdult();
```

静态字段和静态方法属于类本身：

```java
public class SlugUtil {
    public static String normalize(String value) {
        return value.trim().toLowerCase().replace(" ", "-");
    }
}

String slug = SlugUtil.normalize("Hello Java");
```

可把静态工具方法理解为 TS 模块导出的普通工具函数。在 Spring Boot 中，业务服务通常是由 Spring 管理的实例对象，而不是一堆 `static` 方法。

## 11. 继承、接口与抽象类

### 继承：`extends`

```java
public class AdminUser extends User {
    public AdminUser(String name, int age) {
        super(name, age);
    }
}
```

`super(...)` 调用父类构造器。一个类只能继承一个父类。

### 接口：`implements`

```java
public interface Notifier {
    void send(String message);
}

public class EmailNotifier implements Notifier {
    @Override
    public void send(String message) {
        System.out.println("Email: " + message);
    }
}
```

接口接近 TypeScript 的 `interface`：它首先是一个约束。不过 Java 接口是运行时真实存在的类型，也可以有默认方法和静态方法。一个类可以实现多个接口。

```java
Notifier notifier = new EmailNotifier();
notifier.send("欢迎");
```

左边写接口类型，表示调用方只依赖约定，不依赖具体实现。这是后端分层、单元测试和依赖注入常用的做法。

### 抽象类

```java
public abstract class BaseNotifier {
    public abstract void send(String message);

    protected String prefix(String message) {
        return "[Ainame] " + message;
    }
}
```

相关实现确实需要共享字段或公共代码时，使用抽象类；只是表达“具备某种能力/约定”时，优先用接口。

## 12. 数组与集合

数组长度固定：

```java
String[] names = {"Ada", "Grace"};
String first = names[0];
int length = names.length;
```

应用代码更常使用集合：

```java
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

List<String> tags = new ArrayList<>();
tags.add("java");
tags.add("spring");

Set<String> uniqueTags = Set.of("java", "spring");
Map<String, Integer> scores = new HashMap<>();
scores.put("Ada", 95);
```

| Java | JavaScript 对应物 |
| --- | --- |
| `List<T>` | `T[]` |
| `Set<T>` | `Set<T>` |
| `Map<K, V>` | `Map<K, V>` 或 `Record<string, V>` |
| `list.size()` | `array.length` |
| `map.get(key)` | `map.get(key)` |
| `map.put(key, value)` | `map.set(key, value)` |

建议左边使用接口，右边使用具体实现：

```java
List<User> users = new ArrayList<>();
Map<Long, User> usersById = new HashMap<>();
```

这样后续即使换成另一种列表或 Map 实现，调用者大多不需要修改。

### 不可变集合工厂

```java
List<String> roles = List.of("USER", "ADMIN");
Set<String> permissions = Set.of("READ", "WRITE");
Map<String, Integer> config = Map.of("pageSize", 20);
```

`of(...)` 返回的集合不可修改，调用 `add`、`remove`、`put` 会抛异常。需要修改时，用 `new ArrayList<>(roles)` 或 `new HashMap<>(config)` 复制为可变集合。

## 13. 泛型

泛型描述容器处理的元素类型：

```java
List<String> names = new ArrayList<>();
Map<String, User> users = new HashMap<>();
```

它和 TypeScript 泛型是直接对应的：

```typescript
const names: string[] = [];
const users = new Map<string, User>();
```

可以定义泛型类和泛型方法：

```java
public class ApiResponse<T> {
    private final T data;

    public ApiResponse(T data) {
        this.data = data;
    }

    public T getData() {
        return data;
    }
}

public static <T> T first(List<T> values) {
    return values.get(0);
}
```

`ApiResponse<User>` 和 `ApiResponse<List<User>>` 都是合法的。Java 泛型只接收引用类型，不能写 `List<int>`，要写 `List<Integer>`。

## 14. `null` 与 `Optional`

除非 API 特别限制，任何引用类型都可以是 `null`。对 `null` 调用方法会抛出 `NullPointerException`：

```java
String name = null;
// int length = name.length(); // NullPointerException
```

在边界处明确判断：

```java
if (name != null) {
    System.out.println(name.length());
}
```

`Optional<T>` 用于表达“方法可能没有返回值”：

```java
Optional<User> user = userRepository.findById(id);

String displayName = user
    .map(User::getName)
    .orElse("匿名用户");
```

它有点像 TypeScript 的 `User | undefined`，但它是 Java 的容器对象。通常只把它用于返回类型，不建议把它作为实体字段、DTO 字段或方法参数。

## 15. 异常

Java 用异常处理非正常流程：

```java
try {
    User user = userService.findRequired(id);
    return user.getName();
} catch (UserNotFoundException exception) {
    return "未知用户";
} finally {
    auditLog.close();
}
```

自定义异常通常继承某个基础异常：

```java
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(Long id) {
        super("用户不存在：" + id);
    }
}
```

### 受检异常与非受检异常

- `RuntimeException` 及其子类是非受检异常，方法无需声明。
- 其他 `Exception` 子类通常是受检异常，必须捕获或用 `throws` 声明。

```java
public String readFile(Path path) throws IOException {
    return Files.readString(path);
}
```

Spring 业务代码中，常用自定义 `RuntimeException`，再由统一的全局异常处理器转换为 HTTP 响应。

## 16. `record`：不可变数据载体

简单、不可变的数据对象，Java 21 推荐使用 `record`：

```java
public record UserResponse(Long id, String name, String email) {
}

UserResponse response = new UserResponse(1L, "Ada", "ada@example.com");
String name = response.name();
```

Java 会自动生成构造器、访问方法、`equals`、`hashCode` 和 `toString`。访问方法是 `response.name()`，不是 `response.getName()`。

它有点像 TypeScript 的 `type` 或 `interface`，但 `record` 是真正的运行时类。它非常适合作为 API 请求 DTO、响应 DTO、值对象。

## 17. 枚举 `enum`

```java
public enum UserRole {
    USER,
    ADMIN
}

UserRole role = UserRole.ADMIN;
if (role == UserRole.ADMIN) {
    System.out.println("拥有管理员权限");
}
```

Java 枚举比 TypeScript 字符串联合类型更强，它可以定义字段、构造器和方法：

```java
public enum OrderStatus {
    PENDING("待支付"),
    PAID("已支付");

    private final String label;

    OrderStatus(String label) {
        this.label = label;
    }

    public String getLabel() {
        return label;
    }
}
```

## 18. 注解

注解是附加在 Java 代码上的元数据：

```java
@Override
public String toString() {
    return "User";
}
```

编译器、库或框架会读取注解并做相应处理。Spring Boot 大量依赖注解：

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public UserResponse getById(@PathVariable Long id) {
        // ...
    }
}
```

对前端开发者来说，注解可类比装饰器（decorator），但注解本身不会自动产生行为，必须由编译器、框架或运行时反射去读取它。

## 19. Lambda 与方法引用

Java Lambda 用于需要“函数式接口”的位置。函数式接口指只有一个抽象方法的接口。

```java
List<String> names = List.of("Ada", "Grace", "Linus");

names.forEach(name -> System.out.println(name));
names.forEach(System.out::println);
```

`::` 是方法引用：

```text
对象::实例方法
类名::静态方法
类名::new
```

示例：

```java
Function<String, Integer> length = String::length;
Supplier<User> newUser = User::new;
```

被 Lambda 捕获的局部变量必须是 `final` 或“事实上没有重新赋值”：

```java
int minLength = 3;
List<String> longNames = names.stream()
    .filter(name -> name.length() >= minLength)
    .toList();
```

后续不能再给 `minLength` 重新赋值。

## 20. Stream API

Stream 用于以链式方式转换和聚合集合，接近 JS 的 `map`、`filter`、`reduce`：

```java
List<String> upperNames = names.stream()
    .filter(name -> !name.isBlank())
    .map(String::trim)
    .map(String::toUpperCase)
    .toList();
```

对应的 TypeScript 大致是：

```typescript
const upperNames = names
  .filter((name) => name.trim() !== "")
  .map((name) => name.trim())
  .map((name) => name.toUpperCase());
```

常用终止操作：

```java
long count = users.stream().count();
Optional<User> first = users.stream().findFirst();
boolean hasAdmin = users.stream().anyMatch(User::isAdmin);
Map<Long, User> usersById = users.stream()
    .collect(Collectors.toMap(User::getId, Function.identity()));
```

Stream 适合集合转换和汇总。存在复杂分支、副作用、异常处理时，普通 `for` 循环往往更直观，也更容易调试。

## 21. 日期与时间

使用 `java.time`，不要在新代码中主动使用旧的 `java.util.Date`：

```java
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;

Instant now = Instant.now();
LocalDate birthday = LocalDate.of(1998, 5, 12);
LocalDateTime localNow = LocalDateTime.now(ZoneId.of("Asia/Shanghai"));
```

- `Instant`：全球时间线上的明确时间点，适合数据库时间戳和 API。
- `LocalDate`：只有日期，例如生日。
- `LocalDateTime`：日期与时分秒，但没有时区。
- `ZonedDateTime`：包含明确时区的日期时间。

`java.time` 中的对象不可变，避免了旧 `Date` API 的很多问题。

## 22. 你在 Spring Boot 中最常见的语法

### 构造器注入

```java
@Service
public class UserService {
    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}
```

Spring 会创建 `UserRepository`，再创建 `UserService`，并把前者传进构造器。可以理解为框架维护了一张依赖关系图，你不需要到处手动 `new`。

### Controller 与 HTTP 路由

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public UserResponse getUser(@PathVariable Long id) {
        return userService.getUser(id);
    }
}
```

它在概念上接近 Express 注册路由，但 Spring 通过注解发现路由，并且负责 Controller 实例的生命周期。

## 23. Java 与 TypeScript 速查表

| 需求 | Java | TypeScript / JavaScript |
| --- | --- | --- |
| 不可重新赋值 | `final String name` | `const name` |
| 字符串拼接 | `"Hello " + name` 或 `"Hello %s".formatted(name)` | `` `Hello ${name}` `` |
| 可选链 | 显式判空或 `Optional` | `user?.name` |
| 数组转换 | `list.stream().map(...).toList()` | `array.map(...)` |
| 实现接口 | `class X implements Y` | `class X implements Y` |
| API 数据类型 | `record UserDto(...)` | `interface UserDto { ... }` |
| 运行时枚举 | `enum Role { ... }` | 字符串联合或 `enum` |
| 抛出错误 | `throw new IllegalArgumentException()` | `throw new Error()` |
| 导入依赖 | `import java.util.List` | `import { x } from "package"` |
| 命名空间 | `package com.example.app` | 模块路径或包名 |

## 24. 初学阶段应建立的习惯

1. 左侧声明尽量使用最通用且足够的类型：`List<User> users = new ArrayList<>();`。
2. 对不应重新赋值的依赖和变量使用 `final`。
3. 字符串和普通对象比较内容使用 `.equals`；基本类型和枚举比较使用 `==`。
4. 简单不可变的数据优先考虑 `record`。
5. 把可空值当成明确问题处理，不要假设引用一定存在。
6. 方法保持短小，返回类型清晰，避免过深嵌套。
7. 学到一个语法，就在 `ainame-j` 项目里找到它的实际使用位置，再自己改写一个小例子。

## 25. 练习任务

建议按顺序完成，每项开始时都可以只放在一个 Java 文件里：

1. 写一个 `User` 类，包含 `name`、`email`、构造器、Getter，以及 `isEmailVerified()` 方法。
2. 将一个 `UserResponse` 普通类改为 `record`。
3. 创建 `List<User>`，用 `for` 循环输出所有成年人。
4. 将上一步改为 `stream().filter(...).toList()`。
5. 创建 `UserRole` 枚举，用 `switch` 表达式返回不同提示文本。
6. 定义 `MessageSender` 接口，实现 `EmailMessageSender` 和 `ConsoleMessageSender`。
7. 写一个返回 `Optional<User>` 的方法，并在调用方用 `orElse` 提供兜底值。
8. 在 `ainame-j` 中添加一个简单的 `@RestController` 接口，返回一个 `record` DTO。

## 26. 之后的学习顺序

当本文语法已经能读懂并写出时，建议按以下顺序进入后端学习：

1. Maven 与项目目录结构。
2. Spring Boot 的依赖注入与配置。
3. REST Controller、参数校验与统一异常处理。
4. JPA 实体、Repository 与数据库迁移。
5. JUnit、Mockito 与 Spring Boot 测试。
6. Spring Security 与 JWT。

语法只有放进 Controller、Service、Repository、DTO 这些真实职责中才真正好记。阅读 `ainame-j/docs` 中的项目文档时，可以随时回到本文查询对应的语言特性。
