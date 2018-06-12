scalaVersion := "2.11.12"

val nativeImage = taskKey[Unit]("Builds a native image of a benchmark.")
nativeImage := (nativeImage dependsOn (compile in Compile)).value
nativeImage := {
  val graalVMHomeOption = sys.env.get("GRAALVM_HOME")
  val nativeImageFile = graalVMHomeOption.map(p => new java.io.File(p) / "jre" / "bin" / "native-image")
  if(nativeImageFile.isEmpty || nativeImageFile.get.isDirectory()) {
    throw new IllegalArgumentException("GRAALVM_HOME variable is incorrect. GRAALVM_HOME=" + graalVMHomeOption)
  }
  val nativeImagePath: String = nativeImageFile.get.getAbsolutePath

  val cp = (fullClasspath in Compile).value.map(_.data).mkString(java.io.File.pathSeparator)
  val imageCmd = List(nativeImagePath,
    "-classpath", cp,
    "-H:Name=native-image-bench",
    "-H:Path=target",
    ("-H:Class=" + (mainClass in Compile).value.get))
  Process(imageCmd).!
}
