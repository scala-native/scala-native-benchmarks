val lastVersion = "0.4.2"
val versions = List(
  lastVersion
  // "0.4.0",
  // "0.4.1",
)
val scalaVersions = List("2.13")

@main()
def main() = {
  val customRuns = List(
    // s"scala-native-0.4.0-2.11",
    // s"scala-native-0.4.2-SNAPSHOT-2.13",
    // s"scala-native-0.4.0-M2",
    s"scala-native-0.4.0-2.13",
    "scala-native-0.4.3-3"
    // "scala-native-0.4.3-2.13"
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

  // run(List("python3", "scripts/run.py") ++ configsToRun)
  run(List("python3", "scripts/summary.py") ++ configsToRun)
  run(List("python3", "scripts/compiletime-summary.py") ++ configsToRun)

}
