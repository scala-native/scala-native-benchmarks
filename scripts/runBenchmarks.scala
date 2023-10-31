val lastVersion = "0.4.9"
val versions = List(
  lastVersion
  // "0.4.0",
)
val scalaVersions = List("3")

@main()
def main() = {
  val customRuns = List(
    // s"scala-native-0.4.0-2.11",
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
  run(List("python3", "scripts/compiletime-summary.py") ++ configsToRun)

}
