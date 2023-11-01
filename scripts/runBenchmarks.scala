val lastVersion   = "0.4.16"
val versions      = List(lastVersion)
val scalaVersions = List("2.12", "2.13", "3")

@main def RunBechmarks() = {
  val customRuns = List(
    // "scala-native-0.4.16-3",
    // "scala-native-0.5.0-SNAPSHOT-3"
  )
  val standardRuns = for {
    scalaVersion <- scalaVersions
    version      <- versions
  } yield s"scala-native-$version-$scalaVersion"

  val configsToRun = standardRuns ++ customRuns
  println("Config to run:")
  configsToRun.foreach(b => println(" - " + b))
  def run(cmd: Seq[String]) = {
    new java.lang.ProcessBuilder(cmd: _*)
      .inheritIO()
      .start()
      .waitFor()
  }

  run(List("python3", "scripts/run.py") ++ configsToRun)
  run(List("python3", "scripts/summary.py") ++ configsToRun)
  // run(List("python3", "scripts/compiletime-summary.py") ++ configsToRun)

}
