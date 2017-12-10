import scalanative.io.packageNameFromPath

enablePlugins(ScalaNativePlugin)

scalaVersion := "2.11.11"

nativeMode := "release"

nativeGC := "immix"

lazy val nativeBenchmark =
  SettingKey[String]("Only link benchmark that contains given string")

nativeBenchmark := ""

sourceGenerators in Compile += Def.task {
  val dir       = (scalaSource in Compile).value
  val benchmark = nativeBenchmark.value

  assert(benchmark.nonEmpty)
  println(s"Looking for $benchmark in $dir")

  val benchmarks = (dir ** "*Benchmark.scala").get
    .flatMap(IO.relativizeFile(dir, _))
    .map(file => packageNameFromPath(file.toPath))
    .filter(_ != "benchmarks.Benchmark")
    .filter(p => benchmark.isEmpty || p.contains(benchmark + "."))

  println("Discovered benchmarks: " + benchmarks.toList)

  val file = (sourceManaged in Compile).value / "benchmarks" / "Discover.scala"
  IO.write(
    file,
    s"""
    package benchmarks
    object Discover {
      val discovered: Seq[benchmarks.Benchmark[_]] =
        ${benchmarks.mkString("Seq(new ", ", new ", ")")}
    }
  """
  )

  Seq(file)
}
