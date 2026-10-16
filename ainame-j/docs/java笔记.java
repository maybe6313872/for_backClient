// Java中，接口变量只能调用接口中定义的方法，不能调用实现类中特有的方法。下面是一个示例代码：
//接口
interface Run{
    void run();
}
//实现类
class Dog implements Run{
    @Override
    public void run(){
        System.out.println("狗跑");
    }
    public void bark(){
        System.out.println("汪汪");
    }
}

public class Test{
    public static void main(String[] args) {
        //1. 类变量
        Dog dog = new Dog();
        dog.run();
        dog.bark(); // ✅ 可以调用bark，左边是Dog类

        //2. 接口变量
        Run runObj = new Dog();
        runObj.run(); // ✅ 可以
        runObj.bark();// ❌ 编译报错！左边是Run接口，接口没有bark方法
    }
}

// `extends`：**继承类（普通类 / 抽象类）**
// `implements`：**实现接口 interface**

// 1. extends

// 1. 用于：`类 extends 父类`、`接口 extends 别的接口`
// 2. Java **类只能单继承**：一个类只能 `extends 1个类`
// 3. 可以拿到父类的非私有属性、方法，可以重写父类方法

// 2. **implements**

// - 主体：**类实现接口**
// - 数量：一个类可以实现**多个接口**
// - 目的：**承诺实现一套行为规范**，不是父子继承
// - 接口里大多是方法定义（新版可以有 default 静态方法）

// ❌ 不能写：`class A implements 普通类`
// ❌ 不能写：`class A extends 接口`（接口只能被接口 extends）
