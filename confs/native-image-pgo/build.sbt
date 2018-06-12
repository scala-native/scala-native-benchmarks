scalaVersion := "2.11.12"

val instrumentedRuns = settingKey[Int]("The number of instrumented runs.")
instrumentedRuns := 5

val nativeImagePGO = inputKey[Unit]("Builds a native image of a benchmark with profile guided optimizations.")
nativeImagePGO := (nativeImagePGO dependsOn (compile in Compile)).evaluated
nativeImagePGO := {
  val graalVMHomeOption = sys.env.get("GRAALVM_HOME")
  val nativeImageFile = graalVMHomeOption.map(p => new java.io.File(p) / "jre" / "bin" / "native-image")
  if(nativeImageFile.isEmpty || nativeImageFile.get.isDirectory()) {
    throw new IllegalArgumentException("GRAALVM_HOME variable is incorrect. GRAALVM_HOME=" + graalVMHomeOption)
  }
  val nativeImagePath: String = nativeImageFile.get.getAbsolutePath

  val cp = (fullClasspath in Compile).value.map(_.data).mkString(java.io.File.pathSeparator)
  val mainClassName = (mainClass in Compile).value.get
  val instrumentedImageCmd = List(nativeImagePath,
    "--pgo-instrument",
    "-classpath", cp,
    "-H:Path=target",
    "-H:Name=native-image-instrumented-bench",
    "-H:Class=" + mainClassName)
   Process(instrumentedImageCmd).!
   val input = scala.io.Source.fromFile(s"input/${mainClassName}").getLines.mkString
   val output = scala.io.Source.fromFile(s"output/${mainClassName}").getLines.mkString
   val profilePaths = (1 to instrumentedRuns.value) map { i =>
     val fileName = s"target/run$i.iprof"
     val batches = "3000"
     val batch_size = "1"
     Process(List(
       s"target/native-image-instrumented-bench",
       batches,
       batch_size,
       input,
       output,
       "-XX:ProfilesDumpFile=" + fileName
     )).!
     fileName
   }

   val profiles = profilePaths.mkString(",")
   val imageCmd = List(nativeImagePath,
     "--pgo=" + profiles,
     "-classpath", cp,
     "-H:Path=target",
     "-H:Name=native-image-pgo-bench",
     "-H:Class=" + mainClassName)
   Process(imageCmd).!
}

